# Ruby 3 removed Object#tainted?/taint/untrust APIs, but Liquid 4.0.3 still calls them.
# Keep legacy gems usable by providing harmless compatibility shims.
unless "".respond_to?(:tainted?)
  class Object
    def tainted?
      false
    end

    def taint
      self
    end

    def untaint
      self
    end

    def untrust
      self
    end

    def trust
      self
    end
  end
end
